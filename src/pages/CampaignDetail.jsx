import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft,
    Edit2,
    Target,
    Users,
    Zap,
    Calendar,
    BarChart3,
    ChevronRight
} from 'lucide-react';
import { PageHeader, LuxeHeading, LuxeButton, LuxeCard, LuxeBadge, LuxeStat } from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp } from '../utils/animations';
import { campaignService } from '../services/campaignService';
import { toast } from '../components/Toast';

export default function CampaignDetail() {
    const { id } = useParams();
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

    if (loading) return <div className="p-10 text-center">Loading...</div>;
    if (!campaign) return <div className="p-10 text-center">Campaign not found</div>;

    return (
        <motion.div
            className="max-w-6xl mx-auto px-6 py-8 space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Header */}
            <PageHeader
                backUrl="/campaigns"
                title={campaign.name}
                subtitle={`Objective: ${campaign.objective}`}
                action={
                    <div className="flex items-center gap-2">
                        <LuxeBadge variant={
                            campaign.status === 'active' ? 'success' : 'neutral'
                        }>
                            {campaign.status}
                        </LuxeBadge>
                        <LuxeButton variant="secondary" size="sm" icon={Edit2} onClick={() => {}}>Edit</LuxeButton>
                    </div>
                }
            />

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <LuxeStat
                    label="Primary Metric"
                    value={`${campaign.current_value || 0} / ${campaign.target_value}`}
                    icon={Target}
                />
                
                <LuxeStat
                    label="Budget Spent"
                    value={`$${campaign.budget_spent || 0}`}
                    icon={BarChart3}
                />

                <LuxeStat
                    label="Timeline"
                    value={`${campaign.start_date}`}
                    icon={Calendar}
                />

                <LuxeStat
                    label="Health"
                    value="92%"
                    icon={Zap}
                    trend={5}
                />
            </div>

            {/* Performance Summary Placeholder (Task 13) */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-display text-lg font-medium text-neutral-900">Performance Overview</h3>
                </div>
                <LuxeCard className="p-8 flex flex-col items-center justify-center text-center border-dashed bg-neutral-50/50 min-h-[200px]">
                    <BarChart3 className="w-8 h-8 text-neutral-300 mb-3" />
                    <h4 className="font-medium text-neutral-900">Campaign Analytics</h4>
                    <p className="text-sm text-neutral-500 max-w-md">
                        Performance charts and detailed metrics will appear here as the campaign progresses.
                    </p>
                </LuxeCard>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left: Strategy & Config (Task 11) */}
                <div className="space-y-6">
                    <LuxeCard title="Targeting Strategy">
                        <div className="space-y-6">
                            <div>
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-3">Cohorts in Scope</label>
                                <div className="flex flex-col gap-2">
                                    {campaign.cohorts?.map((c, i) => (
                                        <div key={i} className="flex items-center gap-3 p-2 bg-neutral-50 border border-neutral-100 rounded-md">
                                            <div className="w-6 h-6 rounded-full bg-white border border-neutral-200 flex items-center justify-center text-neutral-500">
                                                <Users className="w-3 h-3" />
                                            </div>
                                            <span className="text-sm font-medium text-neutral-700">{c.cohort_id}</span>
                                        </div>
                                    )) || <span className="text-sm text-neutral-400 italic">No cohorts defined</span>}
                                </div>
                            </div>
                            
                            <div className="h-px bg-neutral-100 w-full" />

                            <div>
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-3">Active Channels</label>
                                <div className="flex flex-wrap gap-2">
                                    {campaign.channels?.map((c, i) => (
                                        <LuxeBadge key={i} variant="neutral" icon={Zap} className="pl-2 pr-3 py-1.5 text-xs">
                                            {c.channel}
                                        </LuxeBadge>
                                    )) || <span className="text-sm text-neutral-400 italic">No channels defined</span>}
                                </div>
                            </div>
                        </div>
                    </LuxeCard>
                </div>

                {/* Right: Moves Timeline (Task 12) */}
                <div className="lg:col-span-2">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-display text-lg font-medium text-neutral-900">Move Sequence</h3>
                        <LuxeButton size="sm" icon={Target} variant="secondary">Add Move</LuxeButton>
                    </div>
                    
                    <div className="space-y-3">
                        {/* Mock Moves if none exist */}
                        {(campaign.moves && campaign.moves.length > 0 ? campaign.moves : [
                            { id: 'm1', name: 'Authority Sprint', status: 'completed', type: 'Authority', metric: '45 Leads' },
                            { id: 'm2', name: 'Consideration Sprint', status: 'active', type: 'Consideration', metric: '12 Demos' },
                            { id: 'm3', name: 'Objection Crusher', status: 'planned', type: 'Objection', metric: 'Pending' },
                        ]).map((move, i) => (
                            <Link key={i} to={`/moves/${move.id}`} className="block group">
                                <LuxeCard className="p-0 hover:shadow-md transition-all overflow-hidden border-neutral-200 group-hover:border-neutral-300">
                                    <div className="flex items-stretch">
                                        {/* Status Strip */}
                                        <div className={`w-1.5 shrink-0 ${
                                            move.status === 'completed' ? 'bg-blue-600' : 
                                            move.status === 'active' ? 'bg-green-600' : 
                                            'bg-neutral-200'
                                        }`} />
                                        
                                        <div className="flex-1 p-5 flex items-center justify-between">
                                            <div className="flex items-center gap-5">
                                                <div className="flex flex-col items-center justify-center w-10 h-10 rounded-full bg-neutral-50 border border-neutral-200 shrink-0">
                                                    <span className="text-xs font-bold text-neutral-500">{String(i + 1).padStart(2, '0')}</span>
                                                </div>
                                                
                                                <div>
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <h4 className="font-medium text-neutral-900 text-lg group-hover:text-neutral-700 transition-colors">
                                                            {move.name}
                                                        </h4>
                                                        <LuxeBadge variant={
                                                            move.status === 'active' ? 'success' : 
                                                            move.status === 'completed' ? 'info' : 'neutral'
                                                        } className="ml-2">
                                                            {move.status}
                                                        </LuxeBadge>
                                                    </div>
                                                    <div className="flex items-center gap-3 text-xs text-neutral-500">
                                                        <span className="uppercase tracking-wider font-bold text-neutral-400">{move.type}</span>
                                                        <span className="w-1 h-1 rounded-full bg-neutral-300" />
                                                        <span>Goal: {move.metric || 'TBD'}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <ChevronRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-600 transition-colors" />
                                        </div>
                                    </div>
                                </LuxeCard>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
