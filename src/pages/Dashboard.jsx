import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
    Target,
    TrendingUp,
    Activity,
    Layers,
    ArrowRight,
    Plus,
    BarChart3,
    Sparkles,
    Crosshair,
    Rocket,
    Users
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { LuxeHeading, LuxeButton, LuxeCard, LuxeStat, LuxeBadge } from '../components/ui/PremiumUI'
import { pageTransition, staggerContainer, fadeInUp } from '../utils/animations'

// Get mock data from localStorage or use defaults
const getCampaignsData = () => {
    return [
        {
            id: '1',
            name: 'Q1 Enterprise CTO Conversion',
            status: 'active',
            objective: 'Conversion',
            progress: 65,
            target_cohorts: ['Enterprise CTOs', 'Tech VPs'],
        },
        {
            id: '2',
            name: 'Startup Founder Awareness Sprint',
            status: 'draft',
            objective: 'Awareness',
            progress: 0,
            target_cohorts: ['Startup Founders'],
        },
    ]
}

const getMovesData = () => {
    return [
        {
            id: 1,
            name: 'LinkedIn Authority Campaign',
            campaign: 'Q1 Enterprise CTO Conversion',
            status: 'active',
            progress: 75,
            journey_from: 'Problem Aware',
            journey_to: 'Solution Aware'
        },
        {
            id: 2,
            name: 'Webinar Series Launch',
            campaign: 'Q1 Enterprise CTO Conversion',
            status: 'active',
            progress: 45,
            journey_from: 'Solution Aware',
            journey_to: 'Product Aware'
        },
        {
            id: 3,
            name: 'Content Marketing Push',
            campaign: 'Startup Founder Awareness Sprint',
            status: 'planning',
            progress: 20,
            journey_from: 'Unaware',
            journey_to: 'Problem Aware'
        },
    ]
}

export default function DashboardLuxe() {
    const [campaigns] = useState(getCampaignsData())
    const [moves] = useState(getMovesData())
    const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    }))

    const activeCampaigns = campaigns.filter(c => c.status === 'active')
    const activeMoves = moves.filter(m => m.status === 'active')
    const totalProgress = campaigns.reduce((sum, c) => sum + c.progress, 0) / campaigns.length || 0

    useEffect(() => {
        const interval = setInterval(() => {
            setLastUpdated(new Date().toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }))
        }, 60000)
        return () => clearInterval(interval)
    }, [])

    // Empty state
    if (campaigns.length === 0 && moves.length === 0) {
        return (
            <motion.div
                className="min-h-[80vh] flex items-center justify-center p-6"
                initial="initial"
                animate="animate"
                exit="exit"
                variants={pageTransition}
            >
                <LuxeCard className="max-w-2xl w-full text-center py-16 px-8">
                    <div className="w-20 h-20 rounded-full bg-neutral-50 flex items-center justify-center mx-auto mb-8">
                        <Rocket className="w-10 h-10 text-neutral-400" />
                    </div>
                    <LuxeHeading level={1} className="mb-4">
                        Welcome to Command Center
                    </LuxeHeading>
                    <p className="text-lg text-neutral-500 mb-10 max-w-lg mx-auto">
                        Your strategic war room is ready. Start by defining your positioning, creating campaigns, and launching moves.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <Link to="/strategy/positioning">
                            <LuxeButton icon={Sparkles}>Define Positioning</LuxeButton>
                        </Link>
                        <Link to="/campaigns/new">
                            <LuxeButton variant="secondary" icon={Plus}>Create Campaign</LuxeButton>
                        </Link>
                    </div>
                </LuxeCard>
            </motion.div>
        )
    }

    return (
        <motion.div
            className="space-y-8 max-w-7xl mx-auto px-6 py-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            {/* Header */}
            <motion.div variants={fadeInUp} className="flex items-end justify-between border-b border-neutral-200 pb-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs font-bold uppercase tracking-[0.3em] text-neutral-400">Command Center</span>
                        <span className="h-px w-12 bg-neutral-200" />
                    </div>
                    <LuxeHeading level={1}>Strategic Overview</LuxeHeading>
                </div>
                <div className="text-right hidden md:block">
                    <div className="text-xs text-neutral-400 uppercase tracking-wider mb-1">Last Updated</div>
                    <div className="font-mono text-sm text-neutral-900">{lastUpdated}</div>
                </div>
            </motion.div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <LuxeStat
                    label="Active Campaigns"
                    value={activeCampaigns.length}
                    icon={Layers}
                    delay={0.1}
                />
                <LuxeStat
                    label="Moves in Flight"
                    value={activeMoves.length}
                    icon={Target}
                    delay={0.2}
                />
                <LuxeStat
                    label="Avg Completion"
                    value={`${Math.round(totalProgress)}%`}
                    icon={TrendingUp}
                    trend={12}
                    delay={0.3}
                />
                <LuxeStat
                    label="System Status"
                    value="Online"
                    icon={Activity}
                    delay={0.4}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active Campaigns */}
                <div className="lg:col-span-2 space-y-6">
                    <motion.div variants={fadeInUp} className="flex items-center justify-between">
                        <LuxeHeading level={3}>Active Campaigns</LuxeHeading>
                        <Link to="/campaigns">
                            <LuxeButton variant="ghost" size="sm" icon={ArrowRight}>View All</LuxeButton>
                        </Link>
                    </motion.div>

                    <div className="space-y-4">
                        {campaigns.map((campaign, index) => (
                            <LuxeCard key={campaign.id} delay={0.2 + (index * 0.1)} className="group">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <Link to={`/strategy/campaigns/${campaign.id}`} className="font-serif text-xl text-neutral-900 hover:text-neutral-600 transition-colors">
                                                {campaign.name}
                                            </Link>
                                            <LuxeBadge variant={campaign.status === 'active' ? 'success' : 'neutral'}>
                                                {campaign.status}
                                            </LuxeBadge>
                                        </div>
                                        <div className="flex items-center gap-6 text-sm text-neutral-500">
                                            <span className="flex items-center gap-1.5">
                                                <Target className="w-4 h-4" />
                                                {campaign.objective}
                                            </span>
                                            <span className="flex items-center gap-1.5">
                                                <Users className="w-4 h-4" />
                                                {campaign.target_cohorts?.length || 0} cohorts
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                {campaign.status === 'active' && (
                                    <div>
                                        <div className="flex items-center justify-between text-xs text-neutral-500 mb-2">
                                            <span className="uppercase tracking-wider">Progress</span>
                                            <span className="font-mono">{campaign.progress}%</span>
                                        </div>
                                        <div className="w-full h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${campaign.progress}%` }}
                                                transition={{ duration: 1, delay: 0.5 }}
                                                className="h-full bg-neutral-900"
                                            />
                                        </div>
                                    </div>
                                )}
                            </LuxeCard>
                        ))}
                    </div>
                </div>

                {/* Recent Moves & Quick Actions */}
                <div className="space-y-8">
                    <div className="space-y-6">
                        <motion.div variants={fadeInUp} className="flex items-center justify-between">
                            <LuxeHeading level={3}>Recent Moves</LuxeHeading>
                            <Link to="/moves">
                                <LuxeButton variant="ghost" size="sm">All Moves</LuxeButton>
                            </Link>
                        </motion.div>

                        <div className="space-y-3">
                            {moves.slice(0, 3).map((move, index) => (
                                <LuxeCard key={move.id} delay={0.3 + (index * 0.1)} className="p-4 hover:border-neutral-400">
                                    <div className="mb-2">
                                        <div className="font-medium text-neutral-900 mb-1">{move.name}</div>
                                        <div className="flex items-center gap-2 text-xs text-neutral-500">
                                            <Layers className="w-3 h-3" />
                                            <span className="truncate max-w-[150px]">{move.campaign}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between mt-3">
                                        <LuxeBadge variant={move.status === 'active' ? 'success' : 'neutral'}>
                                            {move.status}
                                        </LuxeBadge>
                                        <span className="text-xs font-mono text-neutral-400">{move.progress}%</span>
                                    </div>
                                </LuxeCard>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <motion.div variants={fadeInUp}>
                            <LuxeHeading level={4} className="mb-4 text-neutral-400 uppercase tracking-widest text-xs">Quick Actions</LuxeHeading>
                        </motion.div>

                        <div className="grid grid-cols-1 gap-3">
                            <Link to="/matrix">
                                <LuxeButton variant="secondary" className="w-full justify-start" icon={BarChart3}>
                                    View Matrix
                                </LuxeButton>
                            </Link>
                            <Link to="/muse">
                                <LuxeButton variant="secondary" className="w-full justify-start" icon={Sparkles}>
                                    Create Content
                                </LuxeButton>
                            </Link>
                            <Link to="/strategy/positioning">
                                <LuxeButton variant="secondary" className="w-full justify-start" icon={Crosshair}>
                                    Refine Strategy
                                </LuxeButton>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    )
}
