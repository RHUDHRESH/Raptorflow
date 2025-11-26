import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
    Target,
    TrendingUp,
    Clock,
    Sparkles,
    ArrowRight,
    CheckCircle2,
    AlertCircle,
    PlayCircle,
    Shield,
    Zap,
    Eye,
    Plus,
    Calendar,
    ChevronRight,
    Award,
    Trophy,
    Star,
    Flame,
    Activity,
    BarChart3,
    Rocket,
    Crosshair,
    Users,
    Layers
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useState, useEffect } from 'react'

// Animated stat counter
const AnimatedCounter = ({ end, duration = 2, suffix = '', prefix = '' }) => {
    const [count, setCount] = useState(0)

    useEffect(() => {
        let startTime = null
        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime
            const progress = Math.min((currentTime - startTime) / (duration * 1000), 1)
            const easeOutQuart = 1 - Math.pow(1 - progress, 4)
            setCount(Math.floor(easeOutQuart * end))

            if (progress < 1) {
                requestAnimationFrame(animate)
            }
        }
        requestAnimationFrame(animate)
    }, [end, duration])

    return <span>{prefix}{count}{suffix}</span>
}

// Get mock data from localStorage or use defaults
const getCampaignsData = () => {
    // In a real app, this would fetch from API or context
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
    // In a real app, this would fetch from API or context
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
            <div className="space-y-8 animate-fade-in">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white border-2 border-black p-12 md:p-20"
                >
                    <div className="max-w-3xl mx-auto text-center space-y-6">
                        <div className="w-20 h-20 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-6">
                            <Rocket className="w-10 h-10 text-neutral-400" />
                        </div>
                        <h1 className="font-serif text-4xl md:text-5xl text-black">
                            Welcome to Your Strategic Command Center
                        </h1>
                        <p className="font-sans text-lg text-neutral-600">
                            Start by defining your positioning, creating campaigns, and launching moves
                        </p>
                        <div className="flex flex-wrap justify-center gap-3 pt-6">
                            <Link to="/strategy/positioning" className="inline-flex items-center gap-2 bg-black text-white px-6 py-3 text-sm font-medium hover:bg-neutral-800 transition-colors">
                                <Sparkles className="w-4 h-4" />
                                Define Positioning
                            </Link>
                            <Link to="/campaigns/new" className="inline-flex items-center gap-2 border-2 border-black text-black px-6 py-3 text-sm font-medium hover:bg-neutral-50 transition-colors">
                                <Plus className="w-4 h-4" />
                                Create Campaign
                            </Link>
                            <Link to="/strategy/cohorts" className="inline-flex items-center gap-2 border-2 border-neutral-200 text-neutral-600 px-6 py-3 text-sm font-medium hover:border-neutral-400 transition-colors">
                                <Users className="w-4 h-4" />
                                Manage Cohorts
                            </Link>
                        </div>
                    </div>
                </motion.div>
            </div>
        )
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Hero Stats */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white border-2 border-black p-8 md:p-12"
            >
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <span className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">Command Center</span>
                            <span className="h-px w-16 bg-neutral-200" />
                        </div>
                        <h1 className="font-serif text-4xl md:text-5xl text-black">
                            Strategic Overview
                        </h1>
                    </div>
                    <div className="text-right">
                        <div className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Last Updated</div>
                        <div className="font-mono text-sm text-neutral-900">{lastUpdated}</div>
                    </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="border-2 border-neutral-200 p-6 hover:border-neutral-900 transition-all"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center">
                                <Layers className="w-5 h-5 text-neutral-900" />
                            </div>
                            <div className="text-xs uppercase tracking-wider text-neutral-500">Campaigns</div>
                        </div>
                        <div className="font-serif text-3xl text-black mb-1">
                            <AnimatedCounter end={campaigns.length} />
                        </div>
                        <div className="text-xs text-neutral-600">
                            {activeCampaigns.length} active
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="border-2 border-neutral-200 p-6 hover:border-neutral-900 transition-all"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center">
                                <Target className="w-5 h-5 text-neutral-900" />
                            </div>
                            <div className="text-xs uppercase tracking-wider text-neutral-500">Moves</div>
                        </div>
                        <div className="font-serif text-3xl text-black mb-1">
                            <AnimatedCounter end={moves.length} />
                        </div>
                        <div className="text-xs text-neutral-600">
                            {activeMoves.length} in progress
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="border-2 border-neutral-200 p-6 hover:border-neutral-900 transition-all"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center">
                                <TrendingUp className="w-5 h-5 text-neutral-900" />
                            </div>
                            <div className="text-xs uppercase tracking-wider text-neutral-500">Progress</div>
                        </div>
                        <div className="font-serif text-3xl text-black mb-1">
                            <AnimatedCounter end={Math.round(totalProgress)} suffix="%" />
                        </div>
                        <div className="text-xs text-neutral-600">
                            Average completion
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="border-2 border-neutral-200 p-6 hover:border-neutral-900 transition-all"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center">
                                <Activity className="w-5 h-5 text-neutral-900" />
                            </div>
                            <div className="text-xs uppercase tracking-wider text-neutral-500">Status</div>
                        </div>
                        <div className="font-serif text-3xl text-black mb-1">
                            {activeCampaigns.length > 0 ? 'Active' : 'Planning'}
                        </div>
                        <div className="text-xs text-neutral-600">
                            System operational
                        </div>
                    </motion.div>
                </div>
            </motion.div>

            {/* Active Campaigns */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-white border-2 border-black p-8"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="font-serif text-2xl text-black">Active Campaigns</h2>
                    <Link to="/campaigns" className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-black transition-colors">
                        View All
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>

                {campaigns.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-4">
                            <Layers className="w-8 h-8 text-neutral-400" />
                        </div>
                        <p className="text-neutral-600 mb-4">No campaigns yet</p>
                        <Link to="/campaigns/new" className="inline-flex items-center gap-2 bg-black text-white px-6 py-3 text-sm font-medium hover:bg-neutral-800 transition-colors">
                            <Plus className="w-4 h-4" />
                            Create Campaign
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {campaigns.map((campaign, index) => (
                            <motion.div
                                key={campaign.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * index }}
                                className="border border-neutral-200 p-6 hover:border-neutral-900 transition-all group"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <Link to={`/strategy/campaigns/${campaign.id}`} className="font-serif text-xl text-black hover:underline">
                                                {campaign.name}
                                            </Link>
                                            <span className={cn(
                                                "px-2 py-1 text-xs rounded",
                                                campaign.status === 'active' ? "bg-green-100 text-green-700" : "bg-neutral-100 text-neutral-600"
                                            )}>
                                                {campaign.status}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-4 text-sm text-neutral-600">
                                            <span className="flex items-center gap-1">
                                                <Target className="w-4 h-4" />
                                                {campaign.objective}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Users className="w-4 h-4" />
                                                {campaign.target_cohorts?.length || 0} cohorts
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                {campaign.status === 'active' && (
                                    <div>
                                        <div className="flex items-center justify-between text-xs text-neutral-500 mb-1">
                                            <span>Progress</span>
                                            <span>{campaign.progress}%</span>
                                        </div>
                                        <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${campaign.progress}%` }}
                                                transition={{ duration: 1, delay: 0.2 * index }}
                                                className="h-full bg-black"
                                            />
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </div>
                )}
            </motion.div>

            {/* Active Moves */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-white border-2 border-black p-8"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="font-serif text-2xl text-black">Recent Moves</h2>
                    <Link to="/moves" className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-black transition-colors">
                        View All
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>

                {moves.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-4">
                            <Target className="w-8 h-8 text-neutral-400" />
                        </div>
                        <p className="text-neutral-600 mb-4">No moves yet</p>
                        <Link to="/moves" className="inline-flex items-center gap-2 bg-black text-white px-6 py-3 text-sm font-medium hover:bg-neutral-800 transition-colors">
                            <Plus className="w-4 h-4" />
                            Create Move
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {moves.slice(0, 5).map((move, index) => (
                            <motion.div
                                key={move.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * index }}
                                className="flex items-center justify-between p-4 border border-neutral-200 hover:border-neutral-900 transition-all"
                            >
                                <div className="flex-1">
                                    <div className="font-medium text-black mb-1">{move.name}</div>
                                    <div className="flex items-center gap-3 text-xs text-neutral-600">
                                        <span className="flex items-center gap-1">
                                            <Layers className="w-3 h-3" />
                                            {move.campaign}
                                        </span>
                                        {move.journey_from && move.journey_to && (
                                            <span className="flex items-center gap-1">
                                                <ArrowRight className="w-3 h-3" />
                                                {move.journey_from} → {move.journey_to}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <div className="text-xs text-neutral-500 mb-1">{move.progress}%</div>
                                        <div className="w-20 h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${move.progress}%` }}
                                                transition={{ duration: 1, delay: 0.1 * index }}
                                                className="h-full bg-black"
                                            />
                                        </div>
                                    </div>
                                    <span className={cn(
                                        "px-2 py-1 text-xs rounded",
                                        move.status === 'active' ? "bg-green-100 text-green-700" : "bg-neutral-100 text-neutral-600"
                                    )}>
                                        {move.status}
                                    </span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </motion.div>

            {/* Quick Actions */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-4"
            >
                <Link to="/matrix" className="group border-2 border-neutral-200 p-6 hover:border-black transition-all">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full bg-neutral-100 group-hover:bg-black transition-colors flex items-center justify-center">
                            <BarChart3 className="w-5 h-5 text-neutral-900 group-hover:text-white transition-colors" />
                        </div>
                        <h3 className="font-serif text-lg text-black">View Matrix</h3>
                    </div>
                    <p className="text-sm text-neutral-600">Analyze performance and insights</p>
                </Link>

                <Link to="/muse" className="group border-2 border-neutral-200 p-6 hover:border-black transition-all">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full bg-neutral-100 group-hover:bg-black transition-colors flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-neutral-900 group-hover:text-white transition-colors" />
                        </div>
                        <h3 className="font-serif text-lg text-black">Create Content</h3>
                    </div>
                    <p className="text-sm text-neutral-600">Draft and repurpose assets</p>
                </Link>

                <Link to="/strategy/positioning" className="group border-2 border-neutral-200 p-6 hover:border-black transition-all">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full bg-neutral-100 group-hover:bg-black transition-colors flex items-center justify-center">
                            <Crosshair className="w-5 h-5 text-neutral-900 group-hover:text-white transition-colors" />
                        </div>
                        <h3 className="font-serif text-lg text-black">Refine Strategy</h3>
                    </div>
                    <p className="text-sm text-neutral-600">Update positioning and messaging</p>
                </Link>
            </motion.div>
        </div>
    )
}
