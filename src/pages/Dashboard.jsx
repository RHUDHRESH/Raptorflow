import { motion, AnimatePresence } from 'framer-motion'
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
    Users,
    CheckCircle2,
    Clock,
    AlertCircle
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { LuxeHeading, LuxeButton, LuxeCard, LuxeStat, LuxeBadge, LuxeSkeleton } from '../components/ui/PremiumUI'
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
    const [isLoading, setIsLoading] = useState(true)
    const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    }))
    const [filterStatus, setFilterStatus] = useState('all')

    const activeCampaigns = campaigns.filter(c => c.status === 'active')
    const activeMoves = moves.filter(m => m.status === 'active')
    const totalProgress = campaigns.reduce((sum, c) => sum + c.progress, 0) / campaigns.length || 0

    const filteredCampaigns = campaigns.filter(c => {
        if (filterStatus === 'all') return true
        return c.status === filterStatus
    })

    useEffect(() => {
        const interval = setInterval(() => {
            setLastUpdated(new Date().toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }))
        }, 60000)

        // Simulate loading
        const timer = setTimeout(() => setIsLoading(false), 1500)

        return () => {
            clearInterval(interval)
            clearTimeout(timer)
        }
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
                role="main"
                aria-label="Empty dashboard state"
            >
                {/* Skip to main content link - Accessibility Fix #4 */}
                <a
                    href="#main-content"
                    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-neutral-900 focus:text-white focus:rounded focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900"
                >
                    Skip to main content
                </a>

                <LuxeCard className="max-w-2xl w-full text-center py-16 px-8" role="article" aria-label="Welcome message">
                    <div className="w-20 h-20 rounded-full bg-neutral-50 flex items-center justify-center mx-auto mb-8" aria-hidden="true">
                        <Rocket className="w-10 h-10 text-neutral-400" />
                    </div>
                    <LuxeHeading level={1} className="mb-4">
                        Welcome to Command Center
                    </LuxeHeading>
                    <p className="text-lg text-neutral-600 mb-10 max-w-lg mx-auto">
                        Your strategic war room is ready. Start by defining your positioning, creating campaigns, and launching moves.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <Link to="/strategy/positioning" className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg">
                            <LuxeButton icon={Sparkles} aria-label="Navigate to define positioning">Define Positioning</LuxeButton>
                        </Link>
                        <Link to="/campaigns/new" className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg">
                            <LuxeButton variant="secondary" icon={Plus} aria-label="Navigate to create new campaign">Create Campaign</LuxeButton>
                        </Link>
                    </div>
                </LuxeCard>
            </motion.div>
        )
    }

    return (
        <motion.div
            id="main-content"
            className="space-y-8 max-w-7xl mx-auto px-6 py-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
            role="main"
            aria-label="Dashboard overview"
        >
            {/* Skip to main content link - Accessibility Fix #4 */}
            <a
                href="#main-content"
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-neutral-900 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900"
            >
                Skip to main content
            </a>

            {/* Loading announcement - Accessibility Fix #5 */}
            <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
                {isLoading ? 'Dashboard is updating...' : 'Dashboard loaded successfully'}
            </div>

            {/* Header */}
            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row sm:items-end justify-between border-b border-neutral-200 pb-6 gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs font-bold uppercase tracking-[0.3em] text-neutral-500">Command Center</span>
                        <span className="h-px w-12 bg-neutral-200" aria-hidden="true" />
                    </div>
                    <LuxeHeading level={1} className="text-3xl sm:text-4xl lg:text-5xl">Strategic Overview</LuxeHeading>
                </div>
                {/* Responsive Fix #6: Show on mobile with adaptive layout */}
                <div className="text-left sm:text-right">
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Last Updated</div>
                    <time className="font-mono text-sm text-neutral-900" dateTime={new Date().toISOString()}>
                        {lastUpdated}
                    </time>
                </div>
            </motion.div>

            {/* Key Metrics - Accessibility Fix #1: Added ARIA labels */}
            {/* Responsive Fix #7: 2-column on tablets, 1-column on mobile */}
            <section aria-label="Key performance metrics" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                {isLoading ? (
                    Array(4).fill(0).map((_, i) => (
                        <LuxeCard key={i} className="h-32">
                            <div className="flex justify-between mb-4">
                                <div className="space-y-2">
                                    <LuxeSkeleton className="h-3 w-24" />
                                    <LuxeSkeleton className="h-8 w-16" />
                                </div>
                                <LuxeSkeleton className="h-10 w-10 rounded-full" />
                            </div>
                        </LuxeCard>
                    ))
                ) : (
                    <>
                        <LuxeStat
                            label="Active Campaigns"
                            value={activeCampaigns.length}
                            icon={Layers}
                            delay={0.1}
                            aria-label={`${activeCampaigns.length} active campaigns`}
                        />
                        <LuxeStat
                            label="Moves in Flight"
                            value={activeMoves.length}
                            icon={Target}
                            delay={0.2}
                            aria-label={`${activeMoves.length} moves currently in progress`}
                        />
                        <LuxeStat
                            label="Avg Completion"
                            value={`${Math.round(totalProgress)}%`}
                            icon={TrendingUp}
                            trend={12}
                            delay={0.3}
                            aria-label={`Average completion rate is ${Math.round(totalProgress)} percent, up 12 percent`}
                        />
                        <LuxeStat
                            label="System Status"
                            value="Online"
                            icon={Activity}
                            delay={0.4}
                            aria-label="System status: Online"
                        />
                    </>
                )}
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active Campaigns */}
                <section className="lg:col-span-2 space-y-6" aria-label="Active campaigns list">
                    <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <LuxeHeading level={3} className="text-2xl sm:text-3xl">Campaigns</LuxeHeading>
                        <div className="flex items-center gap-2">
                            <div className="flex bg-neutral-100 rounded-lg p-1">
                                {['all', 'active', 'draft'].map((status) => (
                                    <button
                                        key={status}
                                        onClick={() => setFilterStatus(status)}
                                        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${filterStatus === status
                                            ? 'bg-white text-neutral-900 shadow-sm'
                                            : 'text-neutral-500 hover:text-neutral-900'
                                            }`}
                                        aria-pressed={filterStatus === status}
                                    >
                                        {status.charAt(0).toUpperCase() + status.slice(1)}
                                    </button>
                                ))}
                            </div>
                            <Link
                                to="/campaigns"
                                className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg min-h-[44px] flex items-center"
                                aria-label="View all campaigns"
                            >
                                <LuxeButton variant="ghost" size="sm" icon={ArrowRight}>
                                    <span className="hidden sm:inline">View All</span>
                                    <span className="sm:hidden">All</span>
                                </LuxeButton>
                            </Link>
                        </div>
                    </motion.div>

                    {isLoading ? (
                        <ul className="space-y-4">
                            {Array(2).fill(0).map((_, i) => (
                                <li key={i}>
                                    <LuxeCard className="h-40">
                                        <div className="space-y-4">
                                            <div className="flex justify-between">
                                                <div className="space-y-2">
                                                    <LuxeSkeleton className="h-6 w-48" />
                                                    <div className="flex gap-2">
                                                        <LuxeSkeleton className="h-4 w-20" />
                                                        <LuxeSkeleton className="h-4 w-20" />
                                                    </div>
                                                </div>
                                                <LuxeSkeleton className="h-6 w-16" />
                                            </div>
                                            <LuxeSkeleton className="h-2 w-full mt-8" />
                                        </div>
                                    </LuxeCard>
                                </li>
                            ))}
                        </ul>
                    ) : filteredCampaigns.length > 0 ? (
                        <ul className="space-y-4" role="list">
                            <AnimatePresence mode='popLayout'>
                                {filteredCampaigns.map((campaign, index) => (
                                    <motion.li
                                        key={campaign.id}
                                        layout
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                        transition={{ duration: 0.2 }}
                                    >
                                        <LuxeCard
                                            delay={0.2 + (index * 0.1)}
                                            className="group focus-within:ring-2 focus-within:ring-neutral-900 focus-within:ring-offset-2 transition-all hover:shadow-lg hover:scale-[1.005] duration-300"
                                            role="article"
                                            aria-label={`Campaign: ${campaign.name}`}
                                        >
                                            <div className="flex items-start justify-between mb-4">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                                                        {/* Responsive Fix #9: Add truncation with tooltip */}
                                                        <Link
                                                            to={`/strategy/campaigns/${campaign.id}`}
                                                            className="font-serif text-lg sm:text-xl text-neutral-900 hover:text-neutral-600 transition-colors focus:outline-none focus:underline focus:decoration-2 focus:underline-offset-4 truncate max-w-full sm:max-w-md min-h-[44px] flex items-center"
                                                            aria-label={`View details for ${campaign.name}`}
                                                            title={campaign.name}
                                                        >
                                                            {campaign.name}
                                                        </Link>
                                                        {/* Visual Hierarchy: Badge Icons */}
                                                        <LuxeBadge
                                                            variant={campaign.status === 'active' ? 'success' : 'neutral'}
                                                            aria-label={`Status: ${campaign.status}`}
                                                        >
                                                            <span className="flex items-center gap-1.5">
                                                                {campaign.status === 'active' ? (
                                                                    <CheckCircle2 className="w-3 h-3" />
                                                                ) : (
                                                                    <Clock className="w-3 h-3" />
                                                                )}
                                                                {campaign.status}
                                                            </span>
                                                        </LuxeBadge>
                                                    </div>
                                                    <div className="flex items-center gap-4 sm:gap-6 text-sm text-neutral-600 flex-wrap">
                                                        <span className="flex items-center gap-1.5">
                                                            <Target className="w-4 h-4" aria-hidden="true" />
                                                            <span aria-label={`Objective: ${campaign.objective}`}>{campaign.objective}</span>
                                                        </span>
                                                        <span className="flex items-center gap-1.5">
                                                            <Users className="w-4 h-4" aria-hidden="true" />
                                                            <span aria-label={`${campaign.target_cohorts?.length || 0} target cohorts`}>
                                                                {campaign.target_cohorts?.length || 0} cohorts
                                                            </span>
                                                        </span>
                                                        <span className="flex items-center gap-1.5 text-neutral-400">
                                                            <Clock className="w-3 h-3" aria-hidden="true" />
                                                            <span>Updated 2h ago</span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            {campaign.status === 'active' && (
                                                <div role="progressbar" aria-valuenow={campaign.progress} aria-valuemin="0" aria-valuemax="100" aria-label="Campaign progress">
                                                    <div className="flex items-center justify-between text-xs text-neutral-600 mb-2">
                                                        <span className="uppercase tracking-wider">Progress</span>
                                                        <span className="font-mono">{campaign.progress}%</span>
                                                    </div>
                                                    <div className="w-full h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                        <motion.div
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${campaign.progress}%` }}
                                                            transition={{ duration: 1, delay: 0.5 }}
                                                            className="h-full bg-neutral-900"
                                                            aria-hidden="true"
                                                        />
                                                    </div>
                                                </div>
                                            )}
                                        </LuxeCard>
                                    </motion.li>
                                ))}
                            </AnimatePresence>
                        </ul>
                    ) : (
                        <LuxeCard className="py-12 text-center">
                            <div className="w-12 h-12 rounded-full bg-neutral-50 flex items-center justify-center mx-auto mb-4">
                                <Layers className="w-6 h-6 text-neutral-400" />
                            </div>
                            <h3 className="text-lg font-medium text-neutral-900 mb-2">No campaigns found</h3>
                            <p className="text-neutral-500 mb-6">No campaigns match the selected filter.</p>
                            <Link to="/campaigns/new">
                                <LuxeButton variant="secondary" size="sm" icon={Plus}>Create Campaign</LuxeButton>
                            </Link>
                        </LuxeCard>
                    )}
                </section>

                {/* Recent Moves & Quick Actions */}
                <div className="space-y-8">
                    <section className="space-y-6" aria-label="Recent tactical moves">
                        <motion.div variants={fadeInUp} className="flex items-center justify-between">
                            <LuxeHeading level={3} className="text-2xl sm:text-3xl">Recent Moves</LuxeHeading>
                            <Link
                                to="/moves"
                                className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg min-h-[44px] flex items-center"
                                aria-label="View all tactical moves"
                            >
                                <LuxeButton variant="ghost" size="sm">
                                    <span className="hidden sm:inline">All Moves</span>
                                    <span className="sm:hidden">All</span>
                                </LuxeButton>
                            </Link>
                        </motion.div>

                        <ul className="space-y-3" role="list">
                            {moves.slice(0, 3).map((move, index) => (
                                <li key={move.id}>
                                    <LuxeCard
                                        delay={0.3 + (index * 0.1)}
                                        className="p-4 hover:border-neutral-400 focus-within:ring-2 focus-within:ring-neutral-900 focus-within:ring-offset-2 transition-all hover:shadow-md hover:scale-[1.01] duration-200"
                                        role="article"
                                        aria-label={`Move: ${move.name}`}
                                    >
                                        <div className="mb-2">
                                            <div className="font-medium text-neutral-900 mb-1 text-sm sm:text-base">{move.name}</div>
                                            <div className="flex items-center gap-2 text-xs text-neutral-600">
                                                <Layers className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
                                                <span
                                                    className="truncate max-w-[150px]"
                                                    title={move.campaign}
                                                    aria-label={`Part of campaign: ${move.campaign}`}
                                                >
                                                    {move.campaign}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center justify-between mt-3">
                                            <LuxeBadge
                                                variant={move.status === 'active' ? 'success' : 'neutral'}
                                                aria-label={`Status: ${move.status}`}
                                            >
                                                <span className="flex items-center gap-1.5">
                                                    {move.status === 'active' ? (
                                                        <Activity className="w-3 h-3" />
                                                    ) : (
                                                        <Clock className="w-3 h-3" />
                                                    )}
                                                    {move.status}
                                                </span>
                                            </LuxeBadge>
                                            <span className="text-xs font-mono text-neutral-600" aria-label={`Progress: ${move.progress} percent`}>
                                                {move.progress}%
                                            </span>
                                        </div>
                                    </LuxeCard>
                                </li>
                            ))}
                        </ul>
                    </section>

                    <section className="space-y-4" aria-label="Quick action shortcuts">
                        <motion.div variants={fadeInUp}>
                            <LuxeHeading level={4} className="mb-4 text-neutral-500 uppercase tracking-widest text-xs">Quick Actions</LuxeHeading>
                        </motion.div>

                        <nav className="grid grid-cols-1 gap-3" aria-label="Quick navigation">
                            <Link
                                to="/matrix"
                                className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg min-h-[44px]"
                                aria-label="Navigate to strategy matrix"
                            >
                                <LuxeButton variant="secondary" className="w-full justify-start h-auto min-h-[44px] py-3 hover:bg-neutral-100 transition-colors" icon={BarChart3}>
                                    View Matrix
                                </LuxeButton>
                            </Link>
                            <Link
                                to="/muse"
                                className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg min-h-[44px]"
                                aria-label="Navigate to content creation"
                            >
                                <LuxeButton variant="secondary" className="w-full justify-start h-auto min-h-[44px] py-3 hover:bg-neutral-100 transition-colors" icon={Sparkles}>
                                    Create Content
                                </LuxeButton>
                            </Link>
                            <Link
                                to="/strategy/positioning"
                                className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 rounded-lg min-h-[44px]"
                                aria-label="Navigate to positioning refinement"
                            >
                                <LuxeButton variant="secondary" className="w-full justify-start h-auto min-h-[44px] py-3 hover:bg-neutral-100 transition-colors" icon={Crosshair}>
                                    Refine Strategy
                                </LuxeButton>
                            </Link>
                        </nav>
                    </section>
                </div>
            </div>
        </motion.div>
    )
}
