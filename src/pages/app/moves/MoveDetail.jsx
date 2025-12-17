import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Calendar,
    Clock,
    Target,
    FileText,
    BarChart3,
    MessageSquare,
    Play,
    Pause,
    MoreHorizontal,
    ChevronLeft
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
 * MoveDetail - Running Move Home with 5 Tabs
 * 
 * Tabs:
 * 1. Today - Single-task execution view
 * 2. Plan - Timeline + checkpoints
 * 3. Assets - Deliverables control center
 * 4. Scoreboard - KPI tracking
 * 5. Review - Checkpoints + AAR
 */

const TABS = [
    { id: 'today', name: 'Today', icon: Play },
    { id: 'plan', name: 'Plan', icon: Calendar },
    { id: 'assets', name: 'Assets', icon: FileText },
    { id: 'scoreboard', name: 'Scoreboard', icon: BarChart3 },
    { id: 'review', name: 'Review', icon: MessageSquare }
]

// Status badge component
const StatusBadge = ({ status }) => {
    const styles = {
        active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
        on_track: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
        at_risk: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
        off_track: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
        completed: 'bg-primary/10 text-primary',
        paused: 'bg-muted text-muted-foreground'
    }

    const labels = {
        active: 'Active',
        on_track: 'On Track',
        at_risk: 'At Risk',
        off_track: 'Off Track',
        completed: 'Completed',
        paused: 'Paused'
    }

    return (
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${styles[status] || styles.active}`}>
            {labels[status] || status}
        </span>
    )
}

const MoveDetail = () => {
    const navigate = useNavigate()
    const { id, tab: urlTab } = useParams()
    const [activeTab, setActiveTab] = useState(urlTab || 'today')

    const {
        moves,
        getCampaign,
        getMoveDayNumber,
        updateMove
    } = useRaptorflowStore()

    const move = moves.find(m => m.id === id)

    if (!move) {
        return (
            <div className="max-w-4xl mx-auto py-12 text-center">
                <p className="text-muted-foreground">Move not found</p>
                <button
                    onClick={() => navigate('/app/moves')}
                    className="mt-4 text-primary hover:underline"
                >
                    Back to Moves
                </button>
            </div>
        )
    }

    // Get associated data
    const campaign = move.campaignId ? getCampaign(move.campaignId) : null
    const currentDay = getMoveDayNumber(move.id) || 1
    const totalDays = move.durationDays || move.plan?.durationDays || 14
    const problem = move.problemType ? PROBLEM_TYPES[move.problemType] : null
    const framework = move.frameworkId ? FRAMEWORK_CONFIGS[move.frameworkId] : null

    // Calculate progress
    const completedTasks = (move.checklistItems || []).filter(t => t.done).length
    const totalTasks = (move.checklistItems || []).length
    const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

    // Determine health status
    const getHealthStatus = () => {
        if (move.status === 'completed') return 'completed'
        if (move.status === 'paused') return 'paused'

        // Based on progress vs day
        const expectedProgress = (currentDay / totalDays) * 100
        if (progress >= expectedProgress - 10) return 'on_track'
        if (progress >= expectedProgress - 25) return 'at_risk'
        return 'off_track'
    }

    const healthStatus = getHealthStatus()

    // Handle tab change
    const handleTabChange = (tabId) => {
        setActiveTab(tabId)
        navigate(`/app/moves/${id}/${tabId}`, { replace: true })
    }

    // Handle pause/resume
    const handleTogglePause = () => {
        updateMove(move.id, {
            status: move.status === 'paused' ? 'active' : 'paused'
        })
    }

    // Render tab content
    const renderTabContent = () => {
        const tabProps = { move, framework, currentDay, totalDays }

        switch (activeTab) {
            case 'today':
                return <TabToday {...tabProps} />
            case 'plan':
                return <TabPlan {...tabProps} />
            case 'assets':
                return <TabAssets {...tabProps} />
            case 'scoreboard':
                return <TabScoreboard {...tabProps} />
            case 'review':
                return <TabReview {...tabProps} />
            default:
                return <TabToday {...tabProps} />
        }
    }

    return (
        <div className="max-w-5xl mx-auto">
            {/* Back button */}
            <button
                onClick={() => navigate('/app/moves')}
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors"
            >
                <ChevronLeft className="w-4 h-4" strokeWidth={1.5} />
                <span className="text-sm">Back to Moves</span>
            </button>

            {/* Move header card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-card border border-border rounded-2xl p-6 mb-6"
            >
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <BrandIcon name="speed" size={24} className="text-primary" />
                        </div>
                        <div>
                            <h1 className="font-serif text-2xl text-foreground mb-1">
                                {move.name || 'Untitled Move'}
                            </h1>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                {framework && (
                                    <span>{framework.name}</span>
                                )}
                                {campaign && (
                                    <>
                                        <span>•</span>
                                        <span>{campaign.name}</span>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleTogglePause}
                            className="p-2.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded-xl transition-colors"
                        >
                            {move.status === 'paused' ? (
                                <Play className="w-5 h-5" strokeWidth={1.5} />
                            ) : (
                                <Pause className="w-5 h-5" strokeWidth={1.5} />
                            )}
                        </button>
                        <button className="p-2.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded-xl transition-colors">
                            <MoreHorizontal className="w-5 h-5" strokeWidth={1.5} />
                        </button>
                    </div>
                </div>

                {/* Problem and stats row */}
                <div className="flex flex-wrap items-center gap-4 mb-4">
                    {problem && (
                        <span className="inline-flex items-center px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
                            {problem.statement}
                        </span>
                    )}
                    <StatusBadge status={healthStatus} />
                </div>

                {/* Stats grid */}
                <div className="grid grid-cols-4 gap-4">
                    <div className="p-3 rounded-xl bg-muted/50">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                            <Calendar className="w-3 h-3" strokeWidth={1.5} />
                            Day
                        </div>
                        <div className="text-lg font-semibold text-foreground">
                            {currentDay} <span className="text-muted-foreground font-normal text-sm">/ {totalDays}</span>
                        </div>
                    </div>

                    <div className="p-3 rounded-xl bg-muted/50">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                            <Target className="w-3 h-3" strokeWidth={1.5} />
                            Progress
                        </div>
                        <div className="text-lg font-semibold text-foreground">
                            {progress}%
                        </div>
                    </div>

                    <div className="p-3 rounded-xl bg-muted/50">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                            <FileText className="w-3 h-3" strokeWidth={1.5} />
                            Tasks
                        </div>
                        <div className="text-lg font-semibold text-foreground">
                            {completedTasks} <span className="text-muted-foreground font-normal text-sm">/ {totalTasks}</span>
                        </div>
                    </div>

                    <div className="p-3 rounded-xl bg-muted/50">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                            <BarChart3 className="w-3 h-3" strokeWidth={1.5} />
                            KPI
                        </div>
                        <div className="text-lg font-semibold text-foreground">
                            {move.tracking?.updates?.length || 0}
                            <span className="text-muted-foreground font-normal text-sm"> logged</span>
                        </div>
                    </div>
                </div>

                {/* Progress bar */}
                <div className="mt-4">
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            className="h-full bg-primary rounded-full"
                        />
                    </div>
                </div>
            </motion.div>

            {/* Tabs */}
            <div className="bg-card border border-border rounded-2xl overflow-hidden">
                <div className="border-b border-border">
                    <div className="flex">
                        {TABS.map((tab) => {
                            const Icon = tab.icon
                            const isActive = activeTab === tab.id

                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => handleTabChange(tab.id)}
                                    className={`
                    flex-1 flex items-center justify-center gap-2 py-4 px-6 text-sm font-medium transition-colors
                    ${isActive
                                            ? 'text-primary border-b-2 border-primary bg-primary/5'
                                            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                                        }
                  `}
                                >
                                    <Icon className="w-4 h-4" strokeWidth={1.5} />
                                    {tab.name}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Tab content */}
                <div className="p-6">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {renderTabContent()}
                    </motion.div>
                </div>
            </div>
        </div>
    )
}

export default MoveDetail
