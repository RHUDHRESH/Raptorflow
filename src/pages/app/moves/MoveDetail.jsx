import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Calendar,
    Target,
    FileText,
    BarChart3,
    MessageSquare,
    Play,
    Pause,
    MoreHorizontal,
    ChevronLeft,
    Zap,
    Flag,
    ShieldAlert,
    TrendingUp
} from 'lucide-react'
import useRaptorflowStore from '../../../store/raptorflowStore'
import { PROBLEM_TYPES, FRAMEWORK_CONFIGS } from '../../../data/frameworkConfigs'
import { BrandIcon } from '@/components/brand/BrandSystem'
import TabToday from './tabs/TabToday'
import TabPlan from './tabs/TabPlan'
import TabAssets from './tabs/TabAssets'
import TabScoreboard from './tabs/TabScoreboard'
import TabReview from './tabs/TabReview'

/**
 * MoveDetail - Running Move Home with 5 Tabs + Strategy Sidebar
 */

const TABS = [
    { id: 'today', name: 'Today', icon: Play },
    { id: 'plan', name: 'Plan', icon: Calendar },
    { id: 'assets', name: 'Assets', icon: FileText },
    { id: 'scoreboard', name: 'Scoreboard', icon: BarChart3 },
    { id: 'review', name: 'Review', icon: MessageSquare }
]

const StatusBadge = ({ status }) => {
    const styles = {
        active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
        paused: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
        completed: 'bg-primary/10 text-primary'
    }
    return (
        <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${styles[status] || styles.active}`}>
            {status}
        </span>
    )
}

const MoveSidebar = ({ move, framework, problem, currentDay, totalDays }) => {
    const slots = move.slots || {}
    const tracking = move.tracking || {}
    const kpi = tracking.metric || framework?.metrics.primary.name || 'Goal'

    // Extract key strategy points if available in inputs
    const inputs = slots.inputs || {}
    // Heuristic to find interesting inputs to show
    const strategyPoints = Object.entries(inputs).slice(0, 3).map(([k, v]) => ({ label: k, value: v }))

    return (
        <div className="space-y-6">
            {/* 1. The Strategy Card */}
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                    <Flag size={12} />
                    Strategy
                </h3>

                <div className="space-y-4">
                    <div>
                        <div className="text-xs font-medium text-muted-foreground mb-1">Objective</div>
                        <div className="text-sm font-medium text-foreground leading-snug">
                            Get {tracking.target || '?'} {kpi} via {framework?.name}
                        </div>
                    </div>

                    <div>
                        <div className="text-xs font-medium text-muted-foreground mb-1">Problem</div>
                        <div className="text-sm text-foreground/80 leading-snug">
                            "{problem?.statement}"
                        </div>
                    </div>

                    {strategyPoints.length > 0 && (
                        <div className="pt-3 border-t border-border mt-3 space-y-3">
                            {strategyPoints.map((p, i) => (
                                <div key={i}>
                                    <div className="text-xs font-medium text-muted-foreground mb-0.5 capitalize">{p.label.replace(/_/g, ' ')}</div>
                                    <div className="text-sm text-foreground italic">"{p.value}"</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* 2. Live Scoreboard */}
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                    <TrendingUp size={12} />
                    Live Scoreboard
                </h3>

                <div className="space-y-4">
                    {/* Primary KPI */}
                    <div className="p-3 bg-muted/30 rounded-lg border border-border/50">
                        <div className="flex justify-between items-end mb-1">
                            <span className="text-xs font-bold text-muted-foreground uppercase">{kpi}</span>
                            <span className="text-xs font-medium text-emerald-600">Target: {tracking.target}</span>
                        </div>
                        <div className="text-2xl font-bold text-foreground">
                            {tracking.updates?.[tracking.updates.length - 1]?.value || tracking.baseline || 0}
                        </div>
                    </div>

                    {/* Leading Indicators */}
                    <div className="space-y-2">
                        {framework?.metrics.leading.map((m, i) => (
                            <div key={i} className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">{m.name}</span>
                                <span className="font-mono text-foreground">--</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* 3. Rules / Guardrails */}
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                    <ShieldAlert size={12} />
                    Rules
                </h3>
                <ul className="space-y-2">
                    {framework?.rules.required.slice(0, 3).map((r, i) => (
                        <li key={i} className="text-xs text-foreground flex items-start gap-2">
                            <span className="text-primary mt-0.5">•</span>
                            {r.label}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
}

const MoveDetail = () => {
    const navigate = useNavigate()
    const { id, tab: activeTab = 'today' } = useParams()

    const {
        moves,
        getCampaign,
        getMoveDayNumber,
        updateMove
    } = useRaptorflowStore()

    const move = moves.find(m => m.id === id)

    if (!move) return <div className="p-12 text-center">Move not found</div>

    const currentDay = getMoveDayNumber(move.id) || 1
    const totalDays = move.durationDays || 14
    const problem = move.problemType ? PROBLEM_TYPES[move.problemType] : null
    const framework = move.frameworkId ? FRAMEWORK_CONFIGS[move.frameworkId] : null

    // Handlers
    const handleTabChange = (tabId) => navigate(`/app/moves/${id}/${tabId}`, { replace: true })
    const handleTogglePause = () => updateMove(move.id, { status: move.status === 'paused' ? 'active' : 'paused' })

    const renderTabContent = () => {
        const props = { move, framework, currentDay, totalDays }
        switch (activeTab) {
            case 'today': return <TabToday {...props} />
            case 'plan': return <TabPlan {...props} />
            case 'assets': return <TabAssets {...props} />
            case 'scoreboard': return <TabScoreboard {...props} />
            case 'review': return <TabReview {...props} />
            default: return <TabToday {...props} />
        }
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
            {/* Top Bar */}
            <div className="flex items-center justify-between mb-8">
                <button
                    onClick={() => navigate('/app/moves')}
                    className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors group"
                >
                    <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                    Back to Moves
                </button>
                <div className="flex items-center gap-3">
                    <StatusBadge status={move.status} />
                    <button onClick={handleTogglePause} className="p-2 bg-card border hover:bg-muted rounded-lg transition-colors">
                        {move.status === 'paused' ? <Play size={16} /> : <Pause size={16} />}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-8 items-start">

                {/* LEFT COLUMN: Main Content */}
                <div className="min-w-0">
                    {/* Move Header */}
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-2">
                            <span className="text-sm font-medium text-primary">Day {currentDay} of {totalDays}</span>
                            <span className="w-1 h-1 rounded-full bg-border" />
                            <span className="text-sm text-muted-foreground">{framework?.name}</span>
                        </div>
                        <h1 className="font-serif text-3xl md:text-4xl text-foreground">
                            {move.name}
                        </h1>
                    </div>

                    {/* Tabs */}
                    <div className="border-b border-border mb-8">
                        <div className="flex overflow-x-auto no-scrollbar">
                            {TABS.map((tab) => {
                                const isActive = activeTab === tab.id
                                const Icon = tab.icon
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => handleTabChange(tab.id)}
                                        className={`
                                            flex items-center gap-2 py-4 px-6 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                                            ${isActive
                                                ? 'border-primary text-primary'
                                                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                                            }
                                        `}
                                    >
                                        <Icon size={16} />
                                        {tab.name}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    {/* Tab Content Canvas */}
                    <div className="min-h-[500px]">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            {renderTabContent()}
                        </motion.div>
                    </div>
                </div>

                {/* RIGHT COLUMN: Strategy Sidebar */}
                <div className="hidden lg:block sticky top-24">
                    <MoveSidebar
                        move={move}
                        framework={framework}
                        problem={problem}
                        currentDay={currentDay}
                        totalDays={totalDays}
                    />
                </div>

            </div>
        </div>
    )
}

export default MoveDetail
